#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, std::string character) {
    for (int i = 0; i < text.size(); i++) {
        if (text[i] == character[0]) {
            text.erase(i, 1);
            return text;
        }
    }
    return text;
}
int main() {
    auto candidate = f;
    assert(candidate(("pn"), ("p")) == ("n"));
}
