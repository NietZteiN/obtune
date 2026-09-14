#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, std::string sep, long num) {
    std::size_t pos = text.find_last_of(sep);
    return text.substr(0, pos) + "___" + text.substr(pos + 1);
}
int main() {
    auto candidate = f;
    assert(candidate(("aa+++bb"), ("+"), (1)) == ("aa++___bb"));
}
