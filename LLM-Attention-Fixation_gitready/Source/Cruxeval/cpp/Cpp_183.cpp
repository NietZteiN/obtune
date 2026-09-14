#include<assert.h>
#include<bits/stdc++.h>
std::vector<std::string> f(std::string text) {
    std::vector<std::string> ls;
    std::stringstream ss(text);
    std::string word;
    while (ss >> word) {
        ls.push_back(word);
    }

    std::vector<std::string> lines;
    std::vector<std::string> res;
    for (size_t i = 0; i < ls.size(); i += 3) {
        lines.push_back(ls[i]);
    }

    for (int i = 0; i < 2; ++i) {
        std::vector<std::string> ln;
        for (size_t j = 1; j < ls.size(); j += 3) {
            ln.push_back(ls[j]);
        }
        if (3 * i + 1 < ln.size()) {
            std::string temp;
            for (size_t k = 3 * i; k < 3 * (i + 1); ++k) {
                temp += ln[k] + " ";
            }
            res.push_back(temp);
        }
    }

    lines.insert(lines.end(), res.begin(), res.end());
    return lines;
}
int main() {
    auto candidate = f;
    assert(candidate(("echo hello!!! nice!")) == (std::vector<std::string>({(std::string)"echo"})));
}
