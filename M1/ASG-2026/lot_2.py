from flask import Flask, render_template, request

app = Flask(__name__)

def longest_common_block(read1: str, read2: str):
    n, m = len(read1), len(read2)

    dp = []
    for i in range(n + 1):
        ligne = []
        for j in range(m + 1):
            ligne.append(0)
        dp.append(ligne)

    max_len = 0
    end_i = end_j = 0

    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if read1[i - 1] == read2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1

                if dp[i][j] > max_len:
                    max_len = dp[i][j]
                    end_i = i - 1
                    end_j = j - 1
            else:
                dp[i][j] = 0

    start_i = end_i - max_len + 1
    start_j = end_j - max_len + 1

    return {
        "score": max_len,
        "block": read1[start_i:end_i + 1],
        "start_i": start_i,
        "start_j": start_j
    }


# print(longest_common_block("AZERTYUIOP","AZDFGHTYUIOHDG"))

@app.route("/", methods=["GET", "POST"])
def index():

    result = None

    if request.method == "POST":

        read1 = request.form["read1"]
        read2 = request.form["read2"]

        result = longest_common_block(read1, read2)

        block = result["block"]

        read1_gras = read1.replace(block, "<b>" + block + "</b>")
        read2_gras = read2.replace(block, "<b>" + block + "</b>")

        result["read1_gras"] = read1_gras
        result["read2_gras"] = read2_gras

    return render_template("index_lot2.html", result=result)


if __name__ == "__main__":
    app.run(debug=True)