#include<assert.h>
#include<bits/stdc++.h>
long f(std::string text, std::string char_str) {
    long position = text.length();
    char char_c = char_str[0];
    if (text.find(char_c) != std::string::npos) {
        position = text.find(char_c);
        if (position > 0) {
            position = (position + 1) % text.length();
        }
    }
    return position;
}
int main() {
    auto candidate = f;
    assert(candidate(("wduhzxlfk"), ("w")) == (0));
}
