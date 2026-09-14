#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text) {
    std::string letters = "";
    for (int i = 0; i < text.length(); i++) {
        if (std::isalnum(text[i])) {
            letters += text[i];
        }
    }
    return letters;
}
int main() {
    auto candidate = f;
    assert(candidate(("we@32r71g72ug94=(823658*!@324")) == ("we32r71g72ug94823658324"));
}
