#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text) {
    std::vector<std::string> texts;
    std::string word;
    std::istringstream iss(text);
    while (iss >> word) {
        texts.push_back(word);
    }

    if (!texts.empty()) {
        std::vector<std::string> xtexts;
        for (const auto& t : texts) {
            if (std::all_of(t.begin(), t.end(), isascii) && t != "nada" && t != "0") {
                xtexts.push_back(t);
            }
        }

        if (!xtexts.empty()) {
            auto max_element = std::max_element(xtexts.begin(), xtexts.end(), 
                [](const std::string& a, const std::string& b) {
                    return a.length() < b.length();
                });
            return *max_element;
        }
        return "nada";
    }

    return "nada";
}
int main() {
    auto candidate = f;
    assert(candidate(("")) == ("nada"));
}
