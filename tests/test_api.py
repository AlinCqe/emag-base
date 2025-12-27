from app.core import get_imgs_from_link, get_link_from_id


def test_get_imgs_from_link():

    supadeziv_imgs_links = {0: 'url:https://s13emagst.akamaized.net/products/75253/75252499/images/res_215e33af0370d7901fd2b5d3332cdcc1.jpg?width=720&height=720&hash=29B5AA3C057AA73373D504F9477494A1', 
                            1: 'url:https://s13emagst.akamaized.net/products/75253/75252499/images/res_ed5d0504ef1e299b3601e2a65b624c3a.jpg?width=720&height=720&hash=A9B521B04523B30E8C07F21631905E38', 
                            2: 'url:https://s13emagst.akamaized.net/products/75253/75252499/images/res_316abb7ecf03f7887874fe172fba6b0a.jpg?width=720&height=720&hash=832806AABAD357AC3E0E4A96BCFF1F55', 
                            3: 'url:https://s13emagst.akamaized.net/products/75253/75252499/images/res_c22bba51b4c37ff038d445ae53ff6ace.jpg?width=720&height=720&hash=AF1A9E62EF59C9861E4EEA3FB711518D', 
                            4: 'url:https://s13emagst.akamaized.net/products/75253/75252499/images/res_3373701f297b543a598854b95ee71743.jpg?width=720&height=720&hash=5276E899EEDDDD85D86C91D17092CC66', 
                            5: 'url:https://s13emagst.akamaized.net/products/75253/75252499/images/res_860f45b74a6f7fe26e84cabe713a1e76.jpg?width=720&height=720&hash=F17D3A7F01FE4E3EF504F85ABD0423E5'}
    
    imgs_scraped_supadeziv = get_imgs_from_link("https://www.emag.ro/cuier-autoadeziv-cu-6-agatatori-nextly-pentru-baie-hol-bucatarie-adeziv-puternic-ajustabil-waterproof-transparent-supadeziv6umer/pd/DWXBF4YBM/")
    
    assert imgs_scraped_supadeziv == supadeziv_imgs_links

    assert imgs_scraped_supadeziv is not None
    assert len(imgs_scraped_supadeziv) == 6

    for v in imgs_scraped_supadeziv.values():
        assert v.startswith("url:https://")

    kinoki_imgs_links = {0:"url:https://s13emagst.akamaized.net/products/63924/63923693/images/res_e6ded82e46c040ccb9676f8cc719e072.jpg?width=720&height=720&hash=03D87105A5E81ADD56C50FF2FB772668",
                         1:"url:https://s13emagst.akamaized.net/products/63924/63923692/images/res_b568b7ee18bef881d8887935f9b0bf16.jpg?width=720&height=720&hash=2AC326827734DD09FAF4B762BD0DAFC6",
                         2:"url:https://s13emagst.akamaized.net/products/63924/63923689/images/res_3a05c6b2a651ef67021b17586d2ee3ad.jpg?width=720&height=720&hash=AE2CD2765590863E02A8DDC6F61961D8",
                         3:"url:https://s13emagst.akamaized.net/products/63924/63923689/images/res_8721a8db73eefb71a35846127f26bf93.jpg?width=720&height=720&hash=75B226EEDB94E84B3FB44C92780400AF"}

    imgs_scraped_kinoki = get_imgs_from_link("https://www.emag.ro/set-10-plasturi-pentru-detoxifiere-si-drenaj-limfatic-kinoki/pd/D46ZDTYBM/")

    assert imgs_scraped_kinoki == kinoki_imgs_links
    assert imgs_scraped_kinoki is not None
    assert len(imgs_scraped_kinoki) == 4
    
    for v in imgs_scraped_kinoki.values():
        assert v.startswith("url:https://")

def test_get_link_from_id():
    assert get_link_from_id("462296047") == "https://www.emag.ro/instalatie-de-craciun-multicolora-nextly-rola-100m-lungime-8-jocuri-de-lumini-rezistenta-la-apa-si-inghet-interior-exterior-pentru-brad-casa-pomi-alimentare-220v-inst-100m-multi/pd/DR9HN5YBM/"
    assert get_link_from_id("462296144") == "https://www.emag.ro/bol-hrana-animale-nextly-hranire-lenta-material-sigur-abs-usor-de-curatat-roz-bol-hrana-mod-r/pd/DVZ4Z63BM/"
    assert get_link_from_id("467299824") == "https://www.emag.ro/bol-hrana-animale-nextly-hranire-lenta-material-sigur-abs-usor-de-curatat-verde-bol-hrana-mod-v/pd/D8N4Z63BM/"

