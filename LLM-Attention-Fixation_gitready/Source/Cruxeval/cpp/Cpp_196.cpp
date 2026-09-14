#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text) {
    std::replace(text.begin(), text.end(), ' ', '.');
    if (std::any_of(text.begin(), text.end(), ::isupper))
        return "correct";
    std::replace(text.begin(), text.end(), '.', ' ');
    return "mixed";
}
int main() {
    auto candidate = f;
    assert(candidate(("398 Is A Poor Year To Sow")) == ("correct"));
}
