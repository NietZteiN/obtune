#include<assert.h>
#include<bits/stdc++.h>
bool f(std::string text, std::string search) {
    return search.rfind(text, 0) == 0;
}
int main() {
    auto candidate = f;
    assert(candidate(("123"), ("123eenhas0")) == (true));
}
