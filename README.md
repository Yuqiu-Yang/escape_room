# A virtual escape room 

![Logo](/assets/logo.png)

This is a simple flask-based web application of a virtual escape room mainly to be used as a pedagogical tool. 

## Try it online 
Currently, the production version of [the app](https://ianyangyuqiu.pythonanywhere.com) is being host on [pythonanywhere](https://pythonanywhere.com). Simply register, login and have fun~~~

## Try it locally 
If you want to build on this project, you can run/test the app on your local machine. Here is how you would this.

- Create a virtual environment. We developed this app using `python=3.8`

```shell 
conda create -n escape_room python=3.8
```

- Install the package 

```shell 
pip install 
```
The dependencies of the app is relatively simple and they should be installed along with the package itself. 
<details>
<summary>Dependencies</summary>

- flask
- jsonschema
</details>

- Run the app locally 

```shell 
flask --app escape_room run --debug
```

## Make your own virtual escape room
The app comes with a pre-configured puzzle. But it's also surprisingly simple to make your own virtual escape room. Currently, this is only accomplishable locally. 

- Clone the repo 

For HTTPS:

```shell 
git clone https://github.com/Yuqiu-Yang/escape_room.git
```

For SSH: 

```shell 
git clone git@github.com:Yuqiu-Yang/escape_room.git
```

- Go to the folder that contains the json file. Suppose you are at the top-level folder `escape_room`

```shell
cd ./escape_room/campaigns
ls -ls 
```
You should be able to see that there is a `game.json` file in the folder. 

Use a similar format, you can then generate your own escape room by changing the storyline, text, answers, images, hints, etc. and of course adding more puzzles. 

For images, you can either use the url to the image online or you can store the images in the static folder. Suppose you are at the top-level folder `escape_room`

```shell
cd ./escape_room/static/puzzle_images
ls -ls
```

## Acknowledgment
This app took inspiration from this [Github repo](https://github.com/csurfer/escaperoom). 