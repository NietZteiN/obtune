#include<assert.h>
#include<bits/stdc++.h>
std::vector<std::string> f(std::string text) {
    std::vector<std::string> text_arr;
    for (int j = 0; j < text.length(); j++) {
        text_arr.push_back(text.substr(j));
    }
    return text_arr;
}
int main() {
    auto candidate = f;
    assert(candidate(("123")) == (std::vector<std::string>({(std::string)"123", (std::string)"23", (std::string)"3"})));
}
