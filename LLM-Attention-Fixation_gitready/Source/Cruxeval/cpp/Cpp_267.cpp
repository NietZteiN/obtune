#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, long space) {
    if (space < 0) {
        return text;
    }
    return text.append(space, ' ');
}
int main() {
    auto candidate = f;
    assert(candidate(("sowpf"), (-7)) == ("sowpf"));
}
