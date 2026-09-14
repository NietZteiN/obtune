#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::vector<std::string> simpons) {
    while (!simpons.empty()) {
        std::string pop = simpons.back();
        simpons.pop_back();
        if (pop == pop[0] + std::string(pop.begin() + 1, pop.end())) {
            return pop;
        }
    }
    return "default_value";
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<std::string>({(std::string)"George", (std::string)"Michael", (std::string)"George", (std::string)"Costanza"}))) == ("Costanza"));
}
