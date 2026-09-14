#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string x) {
    if(std::all_of(x.begin(), x.end(), ::islower)) {
        return x;
    } else {
        std::reverse(x.begin(), x.end());
        return x;
    }
}
int main() {
    auto candidate = f;
    assert(candidate(("ykdfhp")) == ("ykdfhp"));
}
