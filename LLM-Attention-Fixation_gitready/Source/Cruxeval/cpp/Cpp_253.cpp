#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, std::string pref) {
    size_t length = pref.length();
    if (pref == text.substr(0, length)) {
        return text.substr(length);
    }
    return text;
}
int main() {
    auto candidate = f;
    assert(candidate(("kumwwfv"), ("k")) == ("umwwfv"));
}
