#include<assert.h>
#include<bits/stdc++.h>
long f(std::string text) {
    return text.find(",");
}
int main() {
    auto candidate = f;
    assert(candidate(("There are, no, commas, in this text")) == (9));
}
