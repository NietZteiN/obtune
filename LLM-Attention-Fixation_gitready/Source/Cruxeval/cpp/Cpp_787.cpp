#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text) {
    if (text.length() == 0) {
        return "";
    }
    transform(text.begin(), text.end(), text.begin(), ::tolower);
    text[0] = toupper(text[0]);
    return text;
}
int main() {
    auto candidate = f;
    assert(candidate(("xzd")) == ("Xzd"));
}
