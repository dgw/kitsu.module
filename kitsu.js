module.exports = {
    desc: 'Queries the Kitsu API located at https://kitsu.docs.apiary.io',
    usage: 'ka Clannad',
    commands: ['ka', 'kitsu', 'ku'],
    main: function (from, to, text, mes, com) {
        var out = (to === bot.config.nick) ? from : to,
            api = 'https://kitsu.io/api/edge/',
            aFilter = 'anime/?page[limit]=5&filter[text]=',
            uFilter = 'users/?include=waifu&page[limit]=1&filter[name]=',
            sFilter = '/stats/?filter[kind]=anime-amount-consumed',
            lFilter = '/library-entries?page[limit]=3&sort=-progressedAt,updatedAt&include=media&fields[libraryEntries]=status,progress'
        if (com === 'ka' || com === 'kitsu') {
            request(api + aFilter + encodeURIComponent(text), function (error, response, body) {
                if (JSON.parse(body).meta.count === 0) {bot.say(out, '\u000304No results found for "' + text + '"')} else {
                    request(api + 'anime/' + JSON.parse(body).data[0].id, function (error, response, body) {
                        var subType = JSON.parse(body).data.attributes.subtype,
                            title = JSON.parse(body).data.attributes.canonicalTitle,
                            enTitle = JSON.parse(body).data.attributes.titles.en,
                            status = JSON.parse(body).data.attributes.status,
                            count = JSON.parse(body).data.attributes.episodeCount,
                            date = JSON.parse(body).data.attributes.startDate.substring(0,4),
                            slug = JSON.parse(body).data.attributes.slug,
                            synopsis = JSON.parse(body).data.attributes.synopsis.substring(0,350)
                        if (JSON.parse(body).data.attributes.subtype === 'special' || JSON.parse(body).data.attributes.subtype === 'music') {bot.say(out, '\u000304No results found for "' + text + '"')} else {
                            bot.say(out, '\u00030,04[' + subType + ']\u000f ' + title + ' \u000312(\u000f' + enTitle + '\u000312)\u000f -' + ' \u000312(\u000f' + status + '\u000312)\u000f -' + ' \u00030,04' + count + '\u000f Episodes -' + ' Aired \u000312(\u000f' + date + '\u000312)\u000f -' + ' \u00030,06https://kitsu.io/anime/' + slug + '\u000f')
                            bot.say(out, synopsis + '...(cont.)')
                        }
                    })
                }
            })
        }
        if (com === 'ku') {
            request(api + uFilter + encodeURIComponent(text), function (error, response, body) {
                if (JSON.parse(body).meta.count === 0) {bot.say(out, '\u000304Baka! "' + text + '" does not exist!')} else {
                    var uid = JSON.parse(body).data[0].id,
                        userName = JSON.parse(body).data[0].attributes.name,
                        waifuLink = api + 'users/' + uid + '/waifu',
                        statsLink = api + 'users/' + uid + sFilter,
                        libraryLink = api + 'users/' + uid + lFilter
                    request(statsLink, function (error, response, body) {
                        if (JSON.parse(body).meta.count === 0) {bot.say(out, '\u000304The barbarian known as "' + text + '" has never watched anime!')} else {
                            var lwoa = JSON.parse(body).data[0].attributes.statsData.time
                            request(libraryLink, function (error, response, body) {
                                var a0Name = JSON.parse(body).included[0].attributes.canonicalTitle,
                                    a1Name = JSON.parse(body).included[1].attributes.canonicalTitle,
                                    a2Name = JSON.parse(body).included[2].attributes.canonicalTitle,
                                    a0Prog = JSON.parse(body).data[0].attributes.progress,
                                    a1Prog = JSON.parse(body).data[1].attributes.progress,
                                    a2Prog = JSON.parse(body).data[2].attributes.progress
                                request(waifuLink, function (error, response, body) {
                                    if (JSON.parse(body).data != undefined || JSON.parse(body).data != null) {
                                        var waifu = JSON.parse(body).data.attributes.name
                                        bot.say(out, '\u00030,04[' + userName + ']\u000f -' + ' Waifu \u000312(\u000f' + waifu + '\u000312)\u000f -' + ' Life wasted on anime \u00030,04' + lwoa + '\u000f minutes -' + ' \u00030,06https://kitsu.io/users/' + uid + '\u000f')
                                        bot.say(out, '\u00030,04[' + userName + "'s]\u000f recent library updates are: " + a0Name + ' to: ' + a0Prog + ', ' + a1Name + ' to: ' + a1Prog + ', and ' + a2Name + ' to: ' + a2Prog)
                                    } else {
                                        bot.say(out, '\u00030,04[' + userName + ']\u000f -' + ' Has \u000304NO\u000f Waifu -' + ' Life wasted on anime \u00030,04' + lwoa + '\u000f minutes -' + ' \u00030,06https://kitsu.io/users/' + uid + '\u000f')
                                        bot.say(out, '\u00030,04[' + userName + "'s]\u000f recent library updates are: " + a0Name + ' to: ' + a0Prog + ', ' + a1Name + ' to: ' + a1Prog + ', and ' + a2Name + ' to: ' + a2Prog)
                                    }
                                })
                            })
                        }
                    })
                }
            })
        }
    }
}
