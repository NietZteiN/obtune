#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string phrase) {
    std::string result = "";
    for (char& i : phrase) {
        if (!islower(i)) {
            result += i;
        }
    }
    return result;
}
int main() {
    auto candidate = f;
    assert(candidate(("serjgpoDFdbcA.")) == ("DFA."));
}
