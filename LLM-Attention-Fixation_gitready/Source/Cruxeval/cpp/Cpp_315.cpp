#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string challenge) {
    std::transform(challenge.begin(), challenge.end(), challenge.begin(), ::tolower);
    std::replace(challenge.begin(), challenge.end(), 'l', ',');
    return challenge;
}
int main() {
    auto candidate = f;
    assert(candidate(("czywZ")) == ("czywz"));
}
