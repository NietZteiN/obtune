#include<assert.h>
#include<bits/stdc++.h>
std::vector<std::string> f(std::string text) {
    std::vector<std::string> new_text;
    for (size_t i = 0; i < text.size() / 3; ++i) {
        new_text.push_back("< " + text.substr(i * 3, 3) + " level=" + std::to_string(i) + " >");
    }
    std::string last_item = text.substr(text.size() / 3 * 3);
    new_text.push_back("< " + last_item + " level=" + std::to_string(text.size() / 3) + " >");
    return new_text;
}
int main() {
    auto candidate = f;
    assert(candidate(("C7")) == (std::vector<std::string>({(std::string)"< C7 level=0 >"})));
}
