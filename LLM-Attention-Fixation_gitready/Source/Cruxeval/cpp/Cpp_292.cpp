#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text) {
    std::string new_text;
    for (char c : text) {
        new_text += (std::isdigit(c) ? c : '*');
    }
    return new_text;
}
int main() {
    auto candidate = f;
    assert(candidate(("5f83u23saa")) == ("5*83*23***"));
}
