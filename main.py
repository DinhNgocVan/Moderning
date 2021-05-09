from website import create_app

app = create_app()
"only run app if the file is running directly"
if __name__ == '__main__':
    "debug = true every time make change python code app automatically rerun web server"
    app.run(debug=True)
