#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, long count) {
    for (long i = 0; i < count; i++) {
        std::reverse(text.begin(), text.end());
    }
    return text;
}
int main() {
    auto candidate = f;
    assert(candidate(("aBc, ,SzY"), (2)) == ("aBc, ,SzY"));
}
