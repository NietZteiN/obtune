#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text) {
    int index = 1;
    while (index < text.length()) {
        if (text[index] != text[index - 1]) {
            index += 1;
        } else {
            std::string text1 = text.substr(0, index);
            std::string text2 = text.substr(index);
            for (int i = 0; i < text2.length(); i++) {
                if (std::islower(text2[i]))
                    text2[i] = std::toupper(text2[i]);
                else
                    text2[i] = std::tolower(text2[i]);
            }
            return text1 + text2;
        }
    }
    for (int i = 0; i < text.length(); i++) {
        if (std::islower(text[i]))
            text[i] = std::toupper(text[i]);
        else
            text[i] = std::tolower(text[i]);
    }
    return text;
}
int main() {
    auto candidate = f;
    assert(candidate(("USaR")) == ("usAr"));
}
