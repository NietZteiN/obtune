#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text) {
    int count = text.length();
    for (int i = -count + 1; i < 0; i++) {
        text += text[text.length() + i];
    }
    return text;
}
int main() {
    auto candidate = f;
    assert(candidate(("wlace A")) == ("wlace Alc l  "));
}
