#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, std::string froms) {
    text.erase(0, text.find_first_not_of(froms));
    text.erase(text.find_last_not_of(froms) + 1);
    return text;
}
int main() {
    auto candidate = f;
    assert(candidate(("0 t 1cos "), ("st 0	\n  ")) == ("1co"));
}
