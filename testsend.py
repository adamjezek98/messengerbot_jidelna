import message_processor
import sender
import user_manager
import class_scraper

um = user_manager.UserManager()
mp = message_processor.MessageProcessor()
cs = class_scraper.ClassScraper()

ids = [1508122325941445, ]
others = [
    1623311017693123,
    1407440509376782,
    1383771345071477,
    1630494553706357,
    1588783411184314,
    1663761193636650,
    1784654051563355,
    1497613596996413,
    1214203995351036,
    1232574213514876,
    1579962215359597,
    1506681092723950,
    1238311046273484,
    1470861246282786,
    1472511342857064,
    1345194335609901,
    # 1392273284224325, #AK
    1590629744309341,
    1664978863523952,
    2251510828208229,
    1597950870284262,
    1487524074635172,
    1549488461824801,
    1612456825487043,
    1596033747106730,
    1656327254426893,
    1584032914994735,
    2238042996221235,
    1508122325941445,
    1913488295359459,
    1869942066402812,
    1616697931785232,
    1675154029190774,
    1636581496430879,
    1494508860662009, ]


add_others = False

if add_others:
    ids += others

if True:
    for id in ids:
        #sender.send_message(id,"")
        # sender.send_image(id,
        #                 "https://static.planetminecraft.com/files/resource_media/screenshot/1330/Server_Upgrade-704649_6035468.jpg")
        #mp.send_welcome(id)
        cs.send_from_db(id)



