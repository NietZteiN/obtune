#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text) {
    for (std::size_t i = 0; i < text.size(); ++i) {
        if (i == 0 || !std::isalpha(text[i - 1])) {
            text[i] = std::toupper(text[i]);
        } else {
            text[i] = std::tolower(text[i]);
        }
    }
    size_t start_pos = 0;
    while((start_pos = text.find("Io", start_pos)) != std::string::npos) {
        text.replace(start_pos, 2, "io");
        start_pos += 2;
    }
    return text;
}
int main() {
    auto candidate = f;
    assert(candidate(("Fu,ux zfujijabji pfu.")) == ("Fu,Ux Zfujijabji Pfu."));
}
