#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text) {
    for (char& space : text) {
        if (space == ' ') {
            text = text.erase(0, text.find_first_not_of(' '));
        } else {
            text = std::regex_replace(text, std::regex("cd"), std::string(1, space));
        }
    }
    return text;
}
int main() {
    auto candidate = f;
    assert(candidate(("lorem ipsum")) == ("lorem ipsum"));
}
