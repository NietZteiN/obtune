#include<assert.h>
#include<bits/stdc++.h>
bool f(std::string text) {
    return !std::all_of(text.begin(), text.end(), ::isdigit);
}
int main() {
    auto candidate = f;
    assert(candidate(("the speed is -36 miles per hour")) == (true));
}
