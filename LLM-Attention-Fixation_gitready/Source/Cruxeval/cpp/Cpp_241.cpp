#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string postcode) {
    size_t pos = postcode.find('C');
    return postcode.substr(pos);
}
int main() {
    auto candidate = f;
    assert(candidate(("ED20 CW")) == ("CW"));
}
