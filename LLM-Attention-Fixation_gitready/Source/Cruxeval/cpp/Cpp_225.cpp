#include<assert.h>
#include<bits/stdc++.h>
bool f(std::string text) {
    if(std::all_of(text.begin(), text.end(), ::islower)) {
        return true;
    }
    return false;
}
int main() {
    auto candidate = f;
    assert(candidate(("54882")) == (false));
}
