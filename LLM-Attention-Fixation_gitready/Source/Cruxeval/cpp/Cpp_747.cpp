#include<assert.h>
#include<bits/stdc++.h>
bool f(std::string text) {
    if (text == "42.42") {
        return true;
    }
    for (int i = 3; i < text.length() - 3; ++i) {
        if (text[i] == '.' && std::isdigit(text[i - 3]) && std::isdigit(text[i - 2]) && std::isdigit(text[i - 1]) && std::isdigit(text[i + 1]) && std::isdigit(text[i + 2]) && std::isdigit(text[i + 3])) {
            return true;
        }
    }
    return false;
}
int main() {
    auto candidate = f;
    assert(candidate(("123E-10")) == (false));
}
