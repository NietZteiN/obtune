#include<assert.h>
#include<bits/stdc++.h>
union Union_long_std_string{
    long f0;
    std::string f1;    Union_long_std_string(long _f0) : f0(_f0) {}
    Union_long_std_string(std::string _f1) : f1(_f1) {}
    ~Union_long_std_string() {}
    bool operator==(long f) {
        return f0 == f ;
    }    bool operator==(std::string f) {
        return f1 == f ;
    }
};
Union_long_std_string f(std::map<std::string,long> student_marks, std::string name) {
    if (student_marks.find(name) != student_marks.end()) {
        long value = student_marks[name];
        student_marks.erase(name);
        return value;
    }
    return Union_long_std_string("Name unknown");
}
int main() {
    auto candidate = f;
    assert(candidate((std::map<std::string,long>({{"882afmfp", 56}})), ("6f53p")) == "Name unknown");
}
