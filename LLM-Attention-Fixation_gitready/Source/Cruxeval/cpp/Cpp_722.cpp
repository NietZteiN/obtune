#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text) {
    std::string out = "";
    for (int i = 0; i < text.length(); i++) {
        if (isupper(text[i])) {
            out += tolower(text[i]);
        } else {
            out += toupper(text[i]);
        }
    }
    return out;
}
int main() {
    auto candidate = f;
    assert(candidate((",wPzPppdl/")) == (",WpZpPPDL/"));
}
