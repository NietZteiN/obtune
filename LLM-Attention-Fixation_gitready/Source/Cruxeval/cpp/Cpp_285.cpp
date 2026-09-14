#include<assert.h>
#include<bits/stdc++.h>
long f(std::string text, std::string ch) {
    return std::count(text.begin(), text.end(), ch[0]);
}
int main() {
    auto candidate = f;
    assert(candidate(("This be Pirate's Speak for 'help'!"), (" ")) == (5));
}
