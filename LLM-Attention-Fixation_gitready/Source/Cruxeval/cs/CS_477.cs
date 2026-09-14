using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static Tuple<string, string> F(string text) {
        var topicAndProblem = text.Split('|');
        var topic = string.Join("|", topicAndProblem.Take(topicAndProblem.Length - 1));
        var problem = topicAndProblem.Last();

        if (problem == "r")
        {
            problem = topic.Replace("u", "p");
        }

        return new Tuple<string, string>(topic, problem);
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("|xduaisf")).Equals((Tuple.Create("", "xduaisf"))));
    }

}
