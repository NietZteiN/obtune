#include<assert.h>
#include<bits/stdc++.h>
bool f(std::string text, long lower, long upper) {
    return std::all_of(text.begin() + lower, text.begin() + upper, [](unsigned char c) { return isascii(c); });
}
int main() {
    auto candidate = f;
    assert(candidate(("=xtanp|sugv?z"), (3), (6)) == (true));
}
