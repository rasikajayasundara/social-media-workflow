def main():
    print("Hello from social-media-workflow!")

from app.agents import generate_image

print(generate_image("A cute cat", "cat.png"))


if __name__ == "__main__":
    main()
