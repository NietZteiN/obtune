#include<assert.h>
#include<bits/stdc++.h>
bool f(std::string number) {
    return std::all_of(number.begin(), number.end(), ::isdigit);
}
int main() {
    auto candidate = f;
    assert(candidate(("dummy33;d")) == (false));
}
