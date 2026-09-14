#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text) {
    for (int i = 0; i < text.length(); i++) {
        if (islower(text[i])) {
            text[i] = toupper(text[i]);
        } else if (isupper(text[i])) {
            text[i] = tolower(text[i]);
        }
    }
    return text;
}
int main() {
    auto candidate = f;
    assert(candidate(("akA?riu")) == ("AKa?RIU"));
}
