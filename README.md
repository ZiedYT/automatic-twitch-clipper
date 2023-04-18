# Atomatic Twitch Clipper, by ZiedYT
DM me for any issues :)

## Features
- clips a twitch livestream depending on the messages in chat. (eg: spamming the same thing)
- uploads the clip
- sends the clip to chat.

## installation
- Download the repo
- get python (I am using 3.10)
- go to the folder, run `pip install -r requirements.txt`
- install streamlink CLI. https://streamlink.github.io/install.html
- Get your credentials and type them in `secrets.json`:
    - clipperChannel: your twitch name   
    - chatToken: your chat aouth. you can use https://twitchapps.com/tmi/ copy the token
    -  recorderaouth: your twitch player token used to get the stream. 
        - Log out from twitch
        - Log in on Twitch.tv in your web browser
        - Press F12, go to console
        - type `document.cookie.split("; ").find(item=>item.startsWith("auth-token="))?.split("=")[1]`
        - you will get the token back, copy it in the json
    - streamableLogin and streamablePass: your streamable account creds
## Running
- open the directory in cmd
- run `python main.py`, or `python app.py` that provides a simple feedback html page on localhost:8080
## Making your own clippers
- you need to create a new json file {channelname}.json
- there is a class diagram below that describes how it works
- you can also follow the three json files I have provided as an example
- add a `"{channelname}.json":true` in your secrets.json

![Class Diagram](https://cdn-0.plantuml.com/plantuml/png/ZLPVZzis37_tfo3oiXRN1DYhWHOjEWpeSDYAhMzDCJ0MBzPEfZnHlkmMxBjFb2B7HWx3dcAHFrBaZt-Kzn8nn6bmJUTG101WGCiuZkT6Fo1zxM0ICX0zE8y6ka26E5fq0iW6HhMBFGsAIB_GEJkE5AJPAlxZ5VxgTPjTPFZ23pm4FopzxluGpyNyf_IrjbDT-l9gW97ML_xJp8bKuRaXxFfwWa1Z826EW11FDYQLn40ux9fjrsE4WuyjT9wPkYWr9zKqsu54y4XWA2Qb3yqsKEU3eP0kdk-jidFJeNDoSUyiFwetmIS2eUD07Cdai6HtTOH-YdqBptuADRpHuJEbat-aH8eQt1CV5UNoB_Y7cGG1oo395nifsD7oyLUCr48kjG02qoc3WPueFCCIjMlkhFp2pZ8fwrrFtQE0VRWaGG6gEY6pmu_9Mg6QQ-cIB0Qyy90SDtT7YZyJ1f82ZtQWX1h6DwCN6wtdv438AUDpAcz0b7kCCCFVlgruJLD1hrSLtzG2RivDxTbIg-nra6FkM24sMP1hSi3kiPJ-Yp9yuLxFbNB6WTObISw3IhCTCxbM_LMZsZtfizccIpzxYOc65df_WW7vkMIao3cK12lXd7fYm58VAvVmoS0wKUt48ruxCINSUOveEHEebUKe6ZESa3MIxB7PLWDfuTvArDunjekYvHnj7hKZbIhaFj5IInbG5LM2PSysTzsoCS2pmlUiycA8WVA285CdQGvWdT2JDUHX6dNEITEnB16v8_3BUmxe24u1yoX_-FmfJKvHuC7HlJzQRk4g-9q6j6u9-OmYAuG6T_B1D7VfRlJcH-lerODLPEpVvAY-sEWeyLA2qm7AujnAWU8KMEPkqgGQF4WCs4M0ETjpyvMz3aN9-33fjnB_hPaNagxJKhYRkksWsKODOnaxP4dki1RgQae61ofjPRcKwsHZFqzL8cpFTOe-iOvZ2_MiN2TlQbbktRC6q7ilTEq1_qJ1OLuPy_gglIGTCGRhHVV8XoxQ9zqZCmtQ99YbkbCmEaArOveDhuYTShcWiY9Ue7B446kVt92gta_u37XXmqzEwuPvFcVAbU5v8Ze_SQImJk8sn9p4X_jxDR5Hgbdf-fUJg8DRiPl_aqtTG3sviSoqeSDqJ2tH1vA-XVBhdL6pkZ5gIqYpFLas_lIR_PlAdYfd-7fzAxv1z2Kc1Tpuq19dRGlT509np60DioJweidTdekqlW-NvUw7WsNKXfEA_k5Y_UhrRi_5TLv3Tzyhn_d9gb1uyCxvam0kFIKpMDXjYntNwAgjBYbdAEZ3mWikTkjIBokyplZTswXSfx9UgxgCutoTXK1_JZQG0Tqloo5Xpu2QmwqklopIvY9to63emJ81WblgoxE8WMOtqQicoQqiezcpEZcGAaqYBgXoG3QI3_GN3gCZBTHD7Lh0_sOylm0sWkNEJOP4OwbjkqvzpxegZIVXxoBqc6X5VgxOMpPqPYx_Gc6xVLV_khMRFA2RfUxcuMWkuAAipzLAVFjwhjNpVxhc5gY0-TJ2Pls8RfggKjoyC2fkqrI9gcztmHLterA39VbNQDEy9pRJuFu5)