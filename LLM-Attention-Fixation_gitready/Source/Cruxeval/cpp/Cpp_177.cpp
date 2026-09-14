#include <assert.h>
#include <bits/stdc++.h>
std::string f(std::string text) {
    for (int i = 0; i < text.length(); i++) {
        if (i % 2 == 1) {
            if (islower(text[i])) {
                text[i] = toupper(text[i]);
            } else {
                text[i] = tolower(text[i]);
            }
        }
    }
    return text;
}
int main() {
    auto candidate = f;
    assert(candidate(("Hey DUdE THis $nd^ &*&this@#")) == ("HEy Dude tHIs $Nd^ &*&tHiS@#"));
}
