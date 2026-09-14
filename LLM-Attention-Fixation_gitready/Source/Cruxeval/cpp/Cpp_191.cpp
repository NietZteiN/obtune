#include<assert.h>
#include<bits/stdc++.h>
bool f(std::string string) {
    if(std::all_of(string.begin(), string.end(), ::isupper)) {
        return true;
    } else {
        return false;
    }
}
int main() {
    auto candidate = f;
    assert(candidate(("Ohno")) == (false));
}
