#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, long amount) {
    size_t length = text.length();
    std::string pre_text = "|";
    if (amount >= length) {
        int extra_space = amount - length;
        pre_text += std::string(extra_space / 2, ' ');
        return pre_text + text + pre_text;
    }
    return text;
}
int main() {
    auto candidate = f;
    assert(candidate(("GENERAL NAGOOR"), (5)) == ("GENERAL NAGOOR"));
}
