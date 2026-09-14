#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text) {
    std::vector<char> result;
    for (int i = 0; i < text.size(); i++) {
        if (text[i] == tolower(text[i])) {
            continue;
        }
        if (text.size() - 1 - i < text.rfind(tolower(text[i]))) {
            result.push_back(text[i]);
        }
    }
    return std::string(result.begin(), result.end());
}
int main() {
    auto candidate = f;
    assert(candidate(("ru")) == (""));
}
