# -*- coding: utf-8 -*-
import os
import json

from app import create_app

app = create_app()


def main():
    with open('dev-config.json') as f:
        os.environ.update(json.load(f))
    app.run(debug=True)


if __name__ == '__main__':
    main()
