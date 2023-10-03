from PIL import Image, ImageDraw, ImageFont

SOURCE_PATH = "C:/Users/HAWKE-PC/Pictures/dream-world"


font = ImageFont.truetype("fonts/Montserrat/static/Montserrat-Bold.ttf", 48)

im1 = Image.open(SOURCE_PATH + "/348.png")
im2 = Image.open("C:/Users/HAWKE-PC/Pictures/two.png")


w = max(im1.size[0], im2.size[0])
h = max(im1.size[1], im2.size[1])

im = Image.new("RGBA", (w, h))

im.paste(im2, (0, 0))
im.paste(im1, (0, 0), mask=im1)

d = ImageDraw.Draw(im)
d.text((w/2,h-10), "Pinated", fill="white", anchor="ms", font=font)

im.show()