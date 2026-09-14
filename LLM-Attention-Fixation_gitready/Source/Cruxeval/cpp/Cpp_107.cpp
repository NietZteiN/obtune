#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text) {
    std::string result;
    for (int i = 0; i < text.length(); i++) {
        if (!isascii(text[i])) {
            return "";
        } else if (isalnum(text[i])) {
            result += toupper(text[i]);
        } else {
            result += text[i];
        }
    }
    return result;
}
int main() {
    auto candidate = f;
    assert(candidate(("ua6hajq")) == ("UA6HAJQ"));
}
