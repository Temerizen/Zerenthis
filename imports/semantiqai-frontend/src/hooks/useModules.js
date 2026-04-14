import { useMemo } from "react"

export function useModules() {
  return useMemo(
    () => [
      { name: "AI School", route: "/school", group: "learning", blueprint: "Education system" },
      { name: "Cognitive Lab", route: "/cognitive-lab", group: "cognitive", blueprint: "Mental training" },
      { name: "Execution Engine", route: "/execution", group: "execution", blueprint: "Goals and workflows" },
      { name: "Reality Simulation", route: "/simulation", group: "simulation", blueprint: "What-if analysis" },
      { name: "Infinite Creation", route: "/creation", group: "creation", blueprint: "Creative generation" },
      { name: "Founder Control", route: "/founder", group: "founder", blueprint: "Private founder tools" }
    ],
    []
  )
}
