#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, std::string characters) {
    for(int i = 0; i < characters.length(); i++) {
        text.erase(std::find_if(text.rbegin(), text.rend(), [&](char c) { return c != characters[i]; }).base(), text.end());
    }
    return text;
}
int main() {
    auto candidate = f;
    assert(candidate(("r;r;r;r;r;r;r;r;r"), ("x.r")) == ("r;r;r;r;r;r;r;r;"));
}
